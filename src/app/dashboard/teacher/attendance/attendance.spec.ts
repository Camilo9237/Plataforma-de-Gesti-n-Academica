import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Attendance } from './attendance';

describe('Attendance', () => {
  let component: Attendance;
  let fixture: ComponentFixture<Attendance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        Attendance,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Attendance);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
