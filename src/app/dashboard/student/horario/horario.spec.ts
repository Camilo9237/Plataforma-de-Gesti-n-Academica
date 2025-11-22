import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Horario } from './horario';

describe('Horario', () => {
  let component: Horario;
  let fixture: ComponentFixture<Horario>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        Horario,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Horario);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
