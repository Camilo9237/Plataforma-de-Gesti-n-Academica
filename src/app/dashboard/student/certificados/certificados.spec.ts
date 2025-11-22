import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Certificados } from './certificados';

describe('Certificados', () => {
  let component: Certificados;
  let fixture: ComponentFixture<Certificados>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        Certificados,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Certificados);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
